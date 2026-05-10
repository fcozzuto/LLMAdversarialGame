def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev for king moves

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate next cell by strongest resource "advantage"
        best_adv = None
        best_my = None
        for rx, ry in resources:
            d_my = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            adv = d_op - d_my  # positive means we get there no later than opponent
            key = (adv, -d_my)  # prefer higher adv; then prefer smaller d_my
            if best_adv is None or key > (best_adv, best_my):
                best_adv = adv
                best_my = -d_my

        # Global tie-break: prioritize securing (adv>0), then favor reaching earlier, then center-ish
        secure = 1 if best_adv > 0 else 0
        dist_to_best = -best_my  # smaller better
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        val = (secure, best_adv, -dist_to_best, center_bias, -abs(dx) - abs(dy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]