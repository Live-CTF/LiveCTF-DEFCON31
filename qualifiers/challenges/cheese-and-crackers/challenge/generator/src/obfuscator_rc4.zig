const util = @import("util.zig");

pub fn obfuscated_string(comptime str : []const u8) callconv(.Inline) [str.len]u8 {
    const key = @import("options").obfuscation_key;
    var res = comptime obfuscate_string(str, key);
    deobfuscate_string(&res, key);
    return res;
}

fn rc4(dst : []u8, src : []const u8, key : []const u8) void {
    var rc4_state : [256]u8 = undefined;
    
    var i: usize = 0;
    while (i < 256) : (i += 1) { 
        rc4_state[i] =  @intCast(u8, i);
    }

    i = 0;
    var j: usize = 0;
    while (i < 256) : (i += 1) { 
        j = @addWithOverflow(@addWithOverflow(j, rc4_state[i])[0], key[i % key.len])[0] % 256;

        var tmp = rc4_state[i];
        rc4_state[i] = rc4_state[j];
        rc4_state[j] = tmp;
    }
    
    i = 0;
    var ci: usize = 0;
    while (ci < src.len) : (ci += 1) { 
        i = @addWithOverflow(i, 1)[0] % 256;
        j = @addWithOverflow(j, rc4_state[i])[0] % 256;
        var tmp = rc4_state[i];
        rc4_state[i] = rc4_state[j];
        rc4_state[j] = tmp;

        dst[ci] = src[ci] ^ rc4_state[@addWithOverflow(rc4_state[i], rc4_state[j])[0]];
    }
}

noinline fn deobfuscate_string(str : []u8, key : []const u8) void {
    rc4(str, str, key);
}

fn obfuscate_string(comptime str : []const u8, comptime key : []const u8) [str.len]u8 {
    var result_string : [str.len]u8 = undefined;
    
    @setEvalBranchQuota(10000000);
    rc4(&result_string, str, key);
    return result_string;
}
