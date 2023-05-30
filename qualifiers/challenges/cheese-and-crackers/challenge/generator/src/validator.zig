export fn _start(password : *const []const u8) linksection(".text.start") callconv(.C) bool {
    const target_password = @import("options").password;

    comptime var i = 0;
    if(password.*.len != target_password.len) {
        return false;
    }
    inline while(i < target_password.len) : (i += 1) {
        if(password.*[i] != target_password[i]) {
            return false;
        }
    }

    return true;
}
