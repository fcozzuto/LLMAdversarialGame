def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
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
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                move_score += 5000
                continue
            if opd <= 1 and myd <= opd + 1:
                move_score -= 220  # avoid getting there into immediate opponent denial
                continue

            rel = opd - myd  # positive means we are closer than opponent
            inv = 1.0 / (1 + myd)
            # Prefer securing/approaching while still contesting appropriately
            move_score += rel * (120.0 * inv) + (inv * 30.0) - (myd * 4.0)

        # slight bias to reduce distance overall when close competition
        move_score -= cheb(nx, ny, ox, oy) * 0.5

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]