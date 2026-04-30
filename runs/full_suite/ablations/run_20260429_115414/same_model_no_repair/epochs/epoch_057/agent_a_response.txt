def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Select best target resource based on immediate advantage.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        key = (
            1000000 if sd == 0 else 0,
            (od - sd),
            -sd,
            -abs(rx - ox) - abs(ry - oy),
            rx,
            ry,
        )
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d = manh(nx, ny, tx, ty)
        opp_d = manh(ox, oy, tx, ty)

        # Immediate pickup bonus; also block opponent by reducing their relative advantage.
        pickup = 1000000 if (nx, ny) in obstacles else 0
        if (nx, ny) in set(tuple(p) for p in resources):
            pickup = 5000000

        val = 0
        val += pickup
        val += 12 * (opp_d - my_d)
        val += -2 * my_d
        val += -3 * obs_adj(nx, ny)

        # If approaching opponent too closely without advantage, back off slightly.
        sep = manh(nx, ny, ox, oy)
        if sep <= 1 and (opp_d - my_d) < 0:
            val -= 50
        if sep == 0:
            val -= 200

        # Tie-break deterministically by coordinate.
        val += -(abs(nx - tx) + abs(ny - ty)) * 0.001
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move