def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_score(nx, ny):
        if not ok(nx, ny):
            return -10**18
        # Prefer cells near resources where we can "claim" first
        total = 0
        center_bias = 0
        cx, cy = w // 2, h // 2
        center_bias = -0.05 * cd(nx, ny, cx, cy)
        total += center_bias
        best_ours = 10**9
        best_theirs = 10**9
        for rx, ry in resources:
            ds = cd(nx, ny, rx, ry)
            do = cd(ox, oy, rx, ry)
            best_ours = ds if ds < best_ours else best_ours
            best_theirs = do if do < best_theirs else best_theirs
            if ds == 0:
                total += 50.0
                continue
            # If we are closer than opponent to the resource, strongly reward; else mildly penalize
            diff = do - ds
            inv = 1.0 / (1 + ds)
            if diff > 0:
                total += (6.0 + 2.0 * diff) * inv
            else:
                total -= (2.5 + 0.5 * (-diff)) * inv
        # Tactical: if no resources, just approach opponent's direction to cut off
        if not resources:
            total = -cd(nx, ny, ox, oy)
        # Safety: avoid stepping into dead-simple "losing race" when adjacent resource is claimed by them
        # (light touch)
        if resources:
            for rx, ry in resources:
                dso = cd(nx, ny, rx, ry)
                if dso > cd(ox, oy, rx, ry) + 1:
                    total -= 0.2
        # Small deterministic tie-break favoring staying/less movement
        total -= 0.01 * (abs(nx - sx) + abs(ny - sy))
        return total

    best_dx, best_dy = 0, 0
    best_val = -10**18
    # Deterministic iteration order already fixed; ties keep earlier (lexicographic by move list)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = cell_score(nx, ny)
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy
    if not ok(sx + best_dx, sy + best_dy):
        return [0, 0]
    return [int(best_dx), int(best_dy)]