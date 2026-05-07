def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        if resources:
            # Prefer moves that get us closer to a resource than the opponent.
            gain = 0
            best_gap = -10**18
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                gap = (do - ds)  # higher means we are closer than opponent
                if gap > best_gap:
                    best_gap = gap
                    gain = ds
            score = best_gap * 1000 - gain
        else:
            # If no resources are visible, move to maximize distance from opponent.
            score = man(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]