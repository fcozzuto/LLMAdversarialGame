def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick resource where we are ahead, then penalize being near obstacles, then deterministic by coord
    def cell_penalty(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    pen += 1
        return pen

    best = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Higher advantage is good => minimize negative advantage
        adv = od - sd
        key = (-adv, sd - od, cell_penalty(rx, ry), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Choose move that progresses to target while avoiding obstacles (deterministic tie-break)
    sd0 = dist(sx, sy, tx, ty)
    best_move = (10**9, 0, 0, 0)  # (dist, penalty, tie, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        # Prefer moves that reduce distance most; discourage stepping adjacent to obstacles
        pen = cell_penalty(nx, ny)
        tie = 0
        if d == sd0:
            tie = 1  # discourage no-progress
        key = (d, pen, tie, dx, dy)
        if key < best_move:
            best_move = key
    # If all moves blocked, stay
    return [best_move[3], best_move[4]] if best_move[0] != 10**9 else [0, 0]