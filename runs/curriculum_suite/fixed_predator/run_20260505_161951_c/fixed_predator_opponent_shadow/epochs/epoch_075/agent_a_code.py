def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Choose the resource where we become "most advantaged" over opponent next.
        best_r_key = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer immediate collection (sd=0), then prefer being closer than opponent (adv),
            # then prefer smaller sd to actually secure it.
            rkey = (-(0 if sd == 0 else 1), -(od - sd), sd, dist(nx, ny, ox, oy))
            if best_r_key is None or rkey < best_r_key:
                best_r_key = rkey
        # Tie-break across moves by (1) best_r_key, (2) overall closeness to resources, (3) avoid opponent.
        if best_key is None or best_r_key < best_key:
            best_key = best_r_key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]