def choose_move(observation):
    grid = observation.get("grid", {})
    pos = observation.get("position", (0, 0))
    x, y = pos

    moves = [
        (0, 0),
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 1),
        (-1, -1),
        (1, -1),
        (-1, 1),
    ]

    def is_inside(nx, ny):
        w = grid.get("width", 0)
        h = grid.get("height", 0)
        return (0 <= nx < w) and (0 <= ny < h)

    def cell_at(nx, ny):
        return grid.get("cells", {}).get((nx, ny), None)

    def is_empty(nx, ny):
        c = cell_at(nx, ny)
        return c in (None, "")

    def is_resource(nx, ny):
        return cell_at(nx, ny) == "R"

    def is_enemy(nx, ny):
        return cell_at(nx, ny) == "E"

    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not is_inside(nx, ny):
            continue

        score = 0

        if is_empty(nx, ny):
            score += 0
        if is_resource(nx, ny):
            score += 5
        if is_enemy(nx, ny):
            score -= 5

        if dx == 0 and dy == 0:
            score += 0

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        best = (0, 0)

    return [best[0], best[1]]
