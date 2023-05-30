pub const state = extern struct {
    hello: *const fn (u64) callconv(.C) u64,
};
