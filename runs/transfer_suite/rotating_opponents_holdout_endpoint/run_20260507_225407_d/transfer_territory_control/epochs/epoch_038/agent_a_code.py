def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a global deterministic "pressure" point: closest unclaimed, else nearest center.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (abs(t[0] - (w // 2)) + abs(t[1] - (h // 2)), abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        tx, ty = w // 2, h // 2

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # Invalid move => engine keeps position. Still score it deterministically.
            nx, ny = sx, sy

        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 3.0
        elif (nx, ny) in oppT:
            gain += 4.0  # flipping is on entry
        elif (nx, ny) in selfT:
            gain += 0.5

        # Encourage closing to target and also to any adjacent unclaimed/opponent cells.
        dist = abs(nx - tx) + abs(ny - ty)
        gain += -0.15 * dist

        # Micro-lookahead: count how many valuable neighbors we can create from the resulting cell.
        neigh = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                if (ax, ay) in unclaimed:
                    neigh += 1
                elif (ax, ay) in oppT:
                    neigh += 2
        gain += 0.6 * neigh

        # Deterministic tie-break: prefer moves with smaller dx, then dy.
        val = gain
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]