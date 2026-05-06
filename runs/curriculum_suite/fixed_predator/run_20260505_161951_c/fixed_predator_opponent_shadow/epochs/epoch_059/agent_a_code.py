def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if resources:
        best_key = None
        best_move = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            # Prefer moving toward nearest resource; tie-break by farther from opponent
            dres = min(mdist(nx, ny, rx, ry) for rx, ry in resources)
            dob = mdist(nx, ny, ox, oy)
            key = (dres, -dob, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to reduce distance to opponent's position
    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        key = (mdist(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]