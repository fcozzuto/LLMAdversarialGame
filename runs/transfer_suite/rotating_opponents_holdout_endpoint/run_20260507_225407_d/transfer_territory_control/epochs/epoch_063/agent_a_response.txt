def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_val = -10**18
    best_move = (0, 0)
    base_d = dist2(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in self_t:
            v += 1.0
        if (nx, ny) in unclaimed:
            v += 3.0
        if (nx, ny) in opp_t:
            # Flipping on entry: treat as opportunity to convert opponent territory
            v += 2.2

        nd = dist2(nx, ny, ox, oy)
        # Prefer moves that increase distance from opponent (reduce counter-claim pressure)
        v += 0.01 * (nd - base_d)

        # If tied, prefer cells farther from the board center to avoid contested mid
        cx, cy = w // 2, h // 2
        v += 0.001 * (dist2(nx, ny, cx, cy))

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]