const std = @import("std");

const FileSource = std.build.FileSource;

pub fn build(b: *std.build.Builder) !void {
    // Standard target options allows the person running `zig build` to choose
    // what target to build for. Here we do not override the defaults, which
    // means any target is allowed, and the default is native. Other options
    // for restricting supported target set are available.
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    
    const challenge_password: []const u8 = blk: {
        const maybe_password = b.option([]const u8, "password", "The password to solve the crackme");
        if(maybe_password) |password| {
            break :blk password;
        }
        break :blk "TEST_PASSWORD";
    };

    
    const target_arch = target.cpu_arch orelse @import("builtin").target.cpu.arch;

    // Standard release options allow the person running `zig build` to select
    // between Debug, ReleaseSafe, ReleaseFast, and ReleaseSmall.
    //const module_optimize = b.standardOptimizeOption(.{});
    const module_target = std.zig.CrossTarget{
            .cpu_arch = target_arch,
            .os_tag = .freestanding,
            .abi = .none,
    };

    var password_hash: [std.crypto.hash.sha2.Sha256.digest_length]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(challenge_password, &password_hash, .{});

    const validator = b.addExecutable(.{
        .name = b.fmt("validator-{s}-{s}", .{ std.fmt.fmtSliceHexLower(&password_hash), @tagName(target_arch) }),
        .root_source_file = FileSource.relative("src/validator.zig"),
        .target = module_target,
        .optimize = optimize,
    });

    var validator_options = b.addOptions();
    std.log.info("Password: {s}", .{challenge_password});
    validator_options.addOption([]const u8, "password", challenge_password);
    
    validator.strip = true;
    validator.install();
    validator.addOptions("options", validator_options);
    validator.setLinkerScriptPath(.{.path = "src/validator.ld"});

    const blob1 = validator.addObjCopy(.{
        .format = .bin,
        .only_section = ".blob",
        .pad_to = null,
    });

    var obfuscation_key : [32]u8 = undefined;
    std.crypto.random.bytes(&obfuscation_key);

    var options = b.addOptions();
    options.addOption([]const u8, "obfuscation_key", &obfuscation_key);
    
    const exe = b.addExecutable(.{
        .name = b.fmt("challenge-{s}-{s}", .{ std.fmt.fmtSliceHexLower(&password_hash), @tagName(target_arch) }),
        .root_source_file = FileSource.relative("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    exe.step.dependOn(&blob1.step);

    exe.addAnonymousModule("modules/validator", .{
        .source_file = blob1.getOutputSource(),
    });

    exe.addOptions("options", options);
    exe.step.dependOn(&validator.step);
    exe.strip = true;
    exe.install();

    const run_cmd = exe.run();
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| {
        run_cmd.addArgs(args);
    }

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    const exe_tests = b.addTest(.{
        .name = "main-tests",
        .kind = .test_exe,
        .root_source_file =  FileSource.relative("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&exe_tests.step);
}
