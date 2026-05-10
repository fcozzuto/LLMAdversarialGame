def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def norm_cells(key):
        out = []
        for c in observation.get(key) or []:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    out.append((x, y))
        return out

    unclaimed = norm_cells("unclaimed_cells")
    our_t = norm_cells("self_territory")
    opp_t = norm_cells("opponent_territory")

    opp = observation.get("opponent_position")
    ox, oy = (int(opp[0]), int(opp[1])) if opp and len(opp) >= 2 else (None, None)

    def mindist_from(pos, cells, fallback=10**6):
        x, y = pos
        best = fallback
        for a, b in cells:
            d = abs(a - x) + abs(b - y)
            if d < best:
                best = d
                if d == 0:
                    break
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # Aim for unclaimed; prefer staying near our territory if none.
        target_cells = unclaimed if unclaimed else (our_t if our_t else [])
        d_un = mindist_from((nx, ny), target_cells, fallback=0 if not target_cells else 10**6)
        d_our = mindist_from((nx, ny), our_t, fallback=0 if not our_t else 10**6)
        d_opp = mindist_from((nx, ny), opp_t, fallback=0 if not opp_t else 10**6)

        # If opponent position exists, add stronger avoidance.
        d_pos_opp = abs(nx - ox) + abs(ny - oy) if ox is not None else d_opp

        v = 0
        if target_cells:
            v += 1000 - 50 * d_un
        v += 5 * (0 if not our_t else (20 - d_our))
        v -= 120 if d_pos_opp <= 1 else 0
        v -= 30 if d_pos_opp == 2 else 0
        v += 3 if dx == 0 and dy == 0 else 0

        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]