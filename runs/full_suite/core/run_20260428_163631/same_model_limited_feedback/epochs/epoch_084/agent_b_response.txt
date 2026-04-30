def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best_res = None
    best_key = None
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        # Prefer resources I'm closer to; then closer absolute; then deterministic position
        key = (-(opd - myd), myd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_res = r

    tx, ty = best_res
    best_move = (0, 0)
    best_md = None
    # Small deterministic bias to keep pressure toward target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        md = dist((nx, ny), (tx, ty))
        # Prefer smaller distance; then keep path stable toward target; then deterministic tie-break
        key = (md, abs((tx - nx)) + abs((ty - ny)), -dx, -dy, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]