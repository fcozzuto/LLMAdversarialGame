def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_at(nx, ny):
        if (nx, ny) in blocked:
            return -10**9
        res = observation.get("resources", None)
        if isinstance(res, list) and res:
            best = 10**9
            for r in res:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = int(r[0]), int(r[1])
                    if inb(rx, ry) and (rx, ry) not in blocked:
                        d = abs(rx - nx) + abs(ry - ny)
                        if d < best:
                            best = d
            if best == 10**9:
                best = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
            # Prefer closer to resources; slightly avoid getting too close to opponent
            return -best - 0.15 * (abs(nx - ox) + abs(ny - oy))
        # Fallback: prefer center
        cx, cy = (w - 1) / 2, (h - 1) / 2
        return -(abs(nx - cx) + abs(ny - cy)) - 0.05 * (abs(nx - ox) + abs(ny - oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_at(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    dx, dy = best_move
    return [int(dx), int(dy)]