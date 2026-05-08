def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sx, sy = observation.get("self_position", (0, 0))
    sx = int(sx); sy = int(sy)
    ox, oy = observation.get("opponent_position", (0, 0))
    ox = int(ox); oy = int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
                if 0 <= x < w and 0 <= y < h:
                    blocked.add((x, y))
            except:
                pass

    resources = set()
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
                if 0 <= x < w and 0 <= y < h:
                    resources.add((x, y))
            except:
                pass

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
                if 0 <= x < w and 0 <= y < h:
                    unclaimed.add((x, y))
            except:
                pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_s = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        md = abs(nx - ox) + abs(ny - oy)
        s = -md
        if (nx, ny) in resources:
            s += 20
        if (nx, ny) in unclaimed:
            s += 10
        if s > best_s or (s == best_s and (dx, dy) < (best_dx, best_dy)):
            best_s = s
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]