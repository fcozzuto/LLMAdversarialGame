def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # deterministic ordering helps tie-breaking
    moves.sort(key=lambda m: (m[0], m[1]))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)

        if d == 0:
            val = 10**9 if not is_evader else -10**9
        else:
            # prefer moving along/against the line to the opponent
            vx, vy = ox - sx, oy - sy
            wx, wy = nx - sx, ny - sy
            dot = vx * wx + vy * wy
            # small parity term to avoid getting stuck vs zigzag
            parity = (observation.get("turn_index", 0) or 0) & 1
            parity_bias = (1 if (dx + dy + parity) % 2 == 0 else -1)

            # pursuer: minimize distance; evader: maximize distance
            if is_evader:
                val = d + 0.001 * dot + 0.0001 * parity_bias
            else:
                val = -d + 0.001 * dot + 0.0001 * parity_bias

        if best is None or (val > best_val if not is_evader else val > best_val):
            best, best_val = (dx, dy), val

    return [int(best[0]), int(best[1])]