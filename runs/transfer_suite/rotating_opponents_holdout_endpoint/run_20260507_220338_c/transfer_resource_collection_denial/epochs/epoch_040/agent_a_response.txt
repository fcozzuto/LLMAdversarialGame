def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_dx, best_dy, best_val = 0, 0, -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_is_res = 1 if (nx, ny) in resources else 0
        val = 0
        local_best = -10**18

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = opd - myd  # positive => we are closer/equal
            # Prefer grabbing immediately, then winning races; still allow contests if close.
            score = race * 180 - myd * 4 + cell_is_res * 800
            if myd <= 1:
                score += 400
            if race < 0 and myd <= opd + 1:
                score += (opd + 1 - myd) * 120  # contest denials
            if score > local_best:
                local_best = score

        val = local_best
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]