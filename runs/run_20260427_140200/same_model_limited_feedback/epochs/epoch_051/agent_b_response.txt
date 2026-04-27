def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves  # deterministic order

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    best = None
    best_val = None
    for dx, dy in dirs:
        nx = clamp(x + dx, 0, w - 1)
        ny = clamp(y + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            continue

        if resources:
            md = None
            for rx, ry in resources:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md is None or d < md:
                    md = d
        else:
            md = 0

        on_res = 1 if (nx, ny) in res_set else 0
        d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Prefer immediate resource pickup; otherwise approach resources while staying farther from opponent.
        val = 100000 * on_res + (-md) + 0.02 * d_op

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]