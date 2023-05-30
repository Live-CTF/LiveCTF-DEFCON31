const std = @import("std");
const util = @import("util.zig");

pub fn obfuscated_string(comptime str : []const u8) callconv(.Inline) [str.len]u8 {
    const nonce = comptime blk: {
        var nonce : [std.crypto.hash.Blake3.digest_length]u8 = undefined;
        @setEvalBranchQuota(10000000);
        std.crypto.hash.Blake3.hash(str, &nonce, .{.key=null});
        break :blk nonce[0..Salsa20.nonce_length].*;
    };
    const obfuscation_key = comptime blk: {
        var key : [Salsa20.key_length] u8 = undefined;
        std.mem.copy(u8, &key, @import("options").obfuscation_key);
        break :blk key;
    };

    var res = comptime obfuscate_string(str, obfuscation_key, nonce);
    deobfuscate_string(&res, obfuscation_key, nonce);
    return res;
}

const Salsa20 = std.crypto.stream.salsa.Salsa20;

noinline fn deobfuscate_string(str : []u8, key : [Salsa20.key_length] u8, nonce : [Salsa20.nonce_length] u8) void {
    Salsa20.xor(str, str, 0, key, nonce);
}

fn obfuscate_string(comptime str : []const u8, comptime key : [Salsa20.key_length] u8, comptime nonce : [Salsa20.nonce_length] u8) [str.len]u8 {
    var result_string : [str.len]u8 = undefined;
    
    @setEvalBranchQuota(10000000);
    Salsa20.xor(&result_string, str, 0, key, nonce);
    return result_string;
}
