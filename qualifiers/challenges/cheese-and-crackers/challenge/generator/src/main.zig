const std = @import("std");
const obfuscator = @import("obfuscator_rc4.zig");
const util = @import("util.zig");

pub fn main() !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const stdin = std.io.getStdIn().reader();
    const stdout = std.io.getStdOut().writer();
    
    const password = try stdin.readUntilDelimiterOrEofAlloc(allocator, '\n', 256) orelse "";
    
    const module = try call_module(@embedFile("modules/validator"),);
    
    if(module(&password)) {
        _ = try stdout.write("Correct!\n");
    } else {
        _ = try stdout.write("Incorrect!\n");
    }
}

fn call_module(comptime code : []const u8) callconv(.Inline) !*const fn (*const []const u8) bool {
    const deobf_code = obfuscator.obfuscated_string(code);

    const module = try std.os.mmap(null, code.len, std.os.PROT.READ | std.os.PROT.WRITE | std.os.PROT.EXEC, std.os.linux.MAP.ANONYMOUS | std.os.linux.MAP.PRIVATE, -1, 0);
    std.mem.copy(u8, module, &deobf_code);
    return @ptrCast(*const fn (*const []const u8) bool, module.ptr);
}
