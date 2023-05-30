const std = @import("std");

pub fn debug_log(comptime message_level : std.log.Level,  comptime format : []const u8, args : anytype) callconv(.Inline) void {
    if(comptime (@import("builtin").mode == .Debug)) {
        std.log.defaultLog(message_level, .default, format, args);
    }
}
