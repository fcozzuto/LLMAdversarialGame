def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        in_un = 1 if (nx, ny) in unclaimed else 0
        in_self = 1 if (nx, ny) in self_t else 0
        in_opp = 1 if (nx, ny) in opp_t else 0

        dist_opp = abs(nx - ox) + abs(ny - oy)
        adj_opp = 1 if dist_opp == 1 else 0

        score = 0
        score += 50 * in_un
        score += 5 * in_self
        score -= 80 * in_opp
        score -= 20 * adj_opp
        score += 2 * dist_opp

        if unclaimed:
            best_un = 10**9
            for ux, uy in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if d < best_un:
                    best_un = d
            if best_un < 10**9:
                score += max(0, 20 - best_un)

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], dirs.index((t[1], t[2]))))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]