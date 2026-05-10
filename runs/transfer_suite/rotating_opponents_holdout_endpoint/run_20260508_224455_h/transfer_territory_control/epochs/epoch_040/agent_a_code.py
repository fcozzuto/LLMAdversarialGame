def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(c[0]), int(c[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_key = None
    # Prefer moving to reduce Manhattan distance to opponent
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            key = (dist, -nx, -ny)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]

    if best is not None:
        return best

    # Fallback: any legal move (deterministic order)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    return [0, 0]