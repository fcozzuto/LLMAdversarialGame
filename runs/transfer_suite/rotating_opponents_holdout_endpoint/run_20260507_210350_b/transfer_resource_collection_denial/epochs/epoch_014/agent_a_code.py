def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = [tuple(p) for p in observation.get("resources", [])]
    resources = [r for r in resources if r not in obstacles]
    if not resources:
        return [0, 0]

    # Choose resource that we can reach well while limiting opponent advantage.
    my_t = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), man(ox, oy, r[0], r[1])))
    candidates = sorted(resources, key=lambda r: (man(ox, oy, r[0], r[1]) - man(sx, sy, r[0], r[1]),
                                                 man(sx, sy, r[0], r[1])))
    tx, ty = candidates[0] if candidates else my_t

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [ddx, ddy]

    return [0, 0]