def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Base: prefer staying away from opponent
        md_op = abs(nx - ox)
        nd_op = abs(ny - oy)
        d_op = md_op if md_op > nd_op else nd_op  # Chebyshev
        score = d_op * 2

        if resources:
            # Prefer moves that are closer to nearest resource; reward landing on one
            mind = 10**9
            for rx, ry in resources:
                drx = nx - rx
                if drx < 0:
                    drx = -drx
                dry = ny - ry
                if dry < 0:
                    dry = -dry
                d = drx if drx > dry else dry
                if d < mind:
                    mind = d
            if mind == 0:
                score += 1000
            else:
                score += 60 - mind * 5
        else:
            # Drift to center deterministically if no resources visible
            cx, cy = (w - 1) // 2, (h - 1) // 2
            md = abs(nx - cx)
            nd = abs(ny - cy)
            d = md if md > nd else nd
            score += 20 - d

        # Deterministic tie-break: prefer smaller dx, then smaller dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]