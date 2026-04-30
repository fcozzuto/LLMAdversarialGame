def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Move options with deterministic priority
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        # Chebyshev distance for 8-dir moves
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If trapped by obstacles, allow staying
    def best_move_toward(target):
        tx, ty = target
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = dist((nx, ny), (tx, ty))
            opd = dist((ox, oy), (tx, ty))
            # Prefer moves that reduce our distance; if opponent is already closer, prefer larger gap.
            key = (myd, - (opd - myd), abs((nx - ox)) + abs((ny - oy)), dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, [dx, dy]
        return best if best is not None else [0, 0]

    if resources:
        # Strategic change: choose a target where we can improve our "capture advantage"
        best_target = None
        best_score = None
        for r in resources:
            rx, ry = r
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Score favors resources where we are closer or can become closer than opponent.
            # Also slight preference for nearer targets to progress.
            score = (opd - myd, -myd, -(rx + ry))
            if best_score is None or score > best_score:
                best_score, best_target = score, (rx, ry)
        return best_move_toward(best_target)

    # Endgame: no resources—move toward opponent corner to restrict space and potentially block
    # Deterministic: move to reduce distance to opponent while not stepping into obstacles
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dist((nx, ny), (ox, oy)), abs(nx - (w-1)), abs(ny - (h-1)), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [candidates[0][3], candidates[0][4]]