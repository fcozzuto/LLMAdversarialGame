def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    unclaimed = [tuple(p) for p in observation.get("unclaimed_cells", [])]
    candidates = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    valid = []
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    if unclaimed:
        best_t = None
        best_d = None
        for tx, ty in unclaimed:
            d = abs(tx - x) + abs(ty - y)
            if best_d is None or d < best_d or (d == best_d and (tx, ty) < best_t):
                best_d, best_t = d, (tx, ty)
        tx, ty = best_t
        best_move = None
        best_md = None
        for dx, dy in valid:
            nx, ny = x + dx, y + dy
            md = abs(tx - nx) + abs(ty - ny)
            if best_md is None or md < best_md or (md == best_md and (dx, dy) < best_move):
                best_md, best_move = md, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move = None
    best_d = None
    for dx, dy in valid:
        nx, ny = x + dx, y + dy
        d = abs(ox - nx) + abs(oy - ny)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d, best_move = d, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]