def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not legal(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        tx, ty = resources[0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            v = -d * 1000 - (abs(ox - nx) + abs(oy - ny))
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    if unclaimed:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Prefer getting closer to some unclaimed cell while staying away from opponent
            min_u = 10**18
            for ux, uy in unclaimed:
                dd = abs(ux - nx) + abs(uy - ny)
                if dd < min_u:
                    min_u = dd
            v = -(min_u * 10) + (abs(ox - nx) + abs(oy - ny))
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    # Default: move toward increasing distance from opponent (denial) deterministically
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = abs(ox - nx) + abs(oy - ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move