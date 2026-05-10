def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    unclaimed_list = [tuple(c) for c in unclaimed]
    if unclaimed_list:
        top_un = sorted(
            unclaimed_list,
            key=lambda c: (
                man(c[0], c[1], sx, sy) * 2 + man(c[0], c[1], ox, oy)
                - (12 if c in oppT else 0)
                - (8 if c in selfT else 0)
            ),
         )[:18]
    else:
        # No unclaimed: aim for stepping into opponent territory or its boundary
        top_un = []
        for x in range(w):
            for y in range(h):
                if (x, y) in oppT:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in oppT:
                                top_un.append((nx, ny))
        top_un = list(dict.fromkeys(top_un))[:18]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in oppT:
            score = 1000 - man(nx, ny, ox, oy)
        elif (nx, ny) in selfT:
            score = -1
        elif (nx, ny) in top_un:
            score = 80 - man(nx, ny, sx, sy) - (2 * man(nx, ny, ox, oy))
        else:
            # generic progression: drift toward best target or toward center
            if top_un:
                tx, ty = min(top_un, key=lambda c: man(c[0], c[1], nx, ny))
                score = 30 - man(nx, ny, tx, ty) - (man(nx, ny, ox, oy) // 2)
            else:
                cx, cy = w // 2, h // 2
                score = 10 - man(nx, ny, cx, cy) // 2 - man(nx, ny, ox, oy) // 3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]