def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    block = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                block.add((x, y))

    best_t = None
    best_d = 10**9
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in block:
                d = abs(x - sx) + abs(y - sy)
                if d < best_d:
                    best_d = d
                    best_t = (x, y)

    if best_t is None:
        best_t = (ox, oy)

    tx, ty = best_t
    opp_adj = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if 0 <= ox + dx < w and 0 <= oy + dy < h}

    def score(nx, ny):
        if (nx, ny) in block:
            return -10**9
        d = abs(tx - nx) + abs(ty - ny)
        s = -d
        if (nx, ny) in opp_adj:
            s -= 3
        return s

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        sc = score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move