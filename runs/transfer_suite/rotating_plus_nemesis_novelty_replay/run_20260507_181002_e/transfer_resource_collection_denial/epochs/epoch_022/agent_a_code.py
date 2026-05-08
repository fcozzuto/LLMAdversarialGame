def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def to_xy(obj):
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return int(obj[0]), int(obj[1])
        if isinstance(obj, dict):
            q = obj.get("position", obj.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Precompute opponent closeness bias: avoid allowing them to grab the same "next best" cells.
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target_corner_bias = 1 if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else -1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        s = 0
        if (nx, ny) in res:
            s += 2000

        # Evaluate best contested resource from this next step.
        if res:
            local_best = -10**18
            for rx, ry in res:
                self_d = man(nx, ny, rx, ry)
                opp_d = man(nx, ny, rx, ry)  # placeholder overwritten below
                opp_d = man(ox, oy, rx, ry)
                # Prefer resources where we are strictly closer; otherwise reduce priority.
                contest = opp_d - self_d
                # Also prefer moving "forward" in a deterministic diagonal direction.
                forward = (rx + ry) - (sx + sy)
                s_bias = 0.02 * forward * target_corner_bias
                # Soft penalty for being trapped behind obstacles: discourages stepping near obstacles.
                near_obs = 0
                if dx == 0 and dy == 0:
                    near_obs = 0
                else:
                    for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
                        if (ax, ay) in obs:
                            near_obs += 1
                val = contest * 10 - self_d + s_bias - 3 * near_obs
                if val > local_best:
                    local_best = val
            s += local_best

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
        s2 = s - 0.001 * (abs(dx) * 2 + abs(dy))
        if s2 > best_score:
            best_score = s2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]