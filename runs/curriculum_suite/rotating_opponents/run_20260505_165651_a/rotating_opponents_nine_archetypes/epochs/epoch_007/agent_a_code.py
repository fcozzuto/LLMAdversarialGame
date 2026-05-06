def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    edge_opp = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = man(x, y, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # positive means we're closer
        edge_res = (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1)
        # If we're not closer, prioritize intercepting the opponent's closest/edge targets.
        key = (1 if advantage >= 0 else 0,
               advantage + (2 if edge_opp and edge_res else 0),
               -od + (-1 if (edge_opp and edge_res) else 0),
               -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Prefer reducing our distance; if equal, prefer making ourselves relatively closer.
        score = (-sd2, -(od2 - sd2), -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]