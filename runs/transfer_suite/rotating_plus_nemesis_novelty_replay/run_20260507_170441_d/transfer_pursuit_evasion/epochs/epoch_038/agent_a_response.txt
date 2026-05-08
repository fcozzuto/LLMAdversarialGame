def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Immediate capture
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny) and nx == ox and ny == oy:
            return [dx, dy]

    # One-step minimax: assume opponent moves to maximize our distance to it after our move
    best_move = [0, 0]
    best_val = None
    best_tie = None
    for dx, dy in dirs:
        ax, ay = sx + dx, sy + dy
        if not ok(ax, ay):
            continue
        worst = -1
        for odx, ody in dirs:
            bx, by = ox + odx, oy + ody
            if not ok(bx, by):
                continue
            d = man(ax, ay, bx, by)
            if d > worst:
                worst = d
            if worst >= 1000:
                break
        # Tie-breaks: prefer smaller distance after our move, then closer to farthest corner (to corner-trap)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        far_corner_dist = max(man(ox, oy, cx, cy) for (cx, cy) in corners)
        tie = (man(ax, ay, ox, oy), -far_corner_dist)
        val = worst  # opponent tries to maximize this; we minimize it
        if best_val is None or val < best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = [dx, dy]

    # Fallback if all moves blocked (shouldn't happen)
    return best_move