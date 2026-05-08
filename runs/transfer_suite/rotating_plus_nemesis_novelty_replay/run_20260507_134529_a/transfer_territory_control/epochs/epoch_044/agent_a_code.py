def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells") if "unclaimed_cells" in observation else set()

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def best_target():
        candidates = resources or unclaimed
        if candidates:
            return min(candidates, key=lambda p: abs(sx - p[0]) + abs(sy - p[1]))
        if opp_terr:
            return min(opp_terr, key=lambda p: abs(sx - p[0]) + abs(sy - p[1]))
        return (ox, oy)

    tx, ty = best_target()
    best = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        val = -d_self + 0.05 * d_opp
        if (nx, ny) in resources:
            val += 1000
        if (nx, ny) in opp_terr:
            val += 200
        if unclaimed and (nx, ny) in unclaimed:
            val += 300
        if val > best_val or (val == best_val and [dx, dy] < best):
            best_val = val
            best = [dx, dy]

    return best if (0 <= sx + best[0] < w and 0 <= sy + best[1] < h and (sx + best[0], sy + best[1]) not in obstacles) else [0, 0]