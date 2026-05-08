def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox = None if ox is None else int(ox)
    oy = None if oy is None else int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    uc = observation.get("unclaimed_cells") or []
    if uc:
        for p in uc:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
    else:
        st = observation.get("self_territory") or []
        for p in st:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
        if not targets:
            res = observation.get("resources") or []
            for p in res:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < w and 0 <= y < h:
                        targets.append((x, y))

    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    best_t = None
    best_td = 10**9
    for tx, ty in targets or [(sx, sy)]:
        td = man(sx, sy, tx, ty)
        if td < best_td:
            best_td, best_t = td, (tx, ty)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if best_t is None:
            score -= man(nx, ny, sx, sy)
        else:
            score -= man(nx, ny, best_t[0], best_t[1])
        if ox is not None and oy is not None:
            dop = man(nx, ny, ox, oy)
            if dop <= 1:
                score -= 1000
            else:
                score += min(20, dop)  # move away when opponent is close
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]