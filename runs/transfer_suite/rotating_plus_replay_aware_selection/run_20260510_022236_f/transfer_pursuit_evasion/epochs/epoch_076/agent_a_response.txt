def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Deterministic target for evader: farthest corner from opponent.
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inside(x, y)

    def obstacle_risk(x, y):
        # Prefer cells with more free local neighbors.
        free = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and (nx, ny) not in obstacles:
                    free += 1
        return free  # higher is better

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            score = -10**9 if is_evader else 10**9
        else:
            dist_opp = abs(nx - ox) + abs(ny - oy)
            risk = obstacle_risk(nx, ny)
            if is_evader:
                # Run away; also bias toward the far corner to force predictable separation.
                dist_corner = abs(nx - tx) + abs(ny - ty)
                score = dist_opp * 10 + dist_corner * 3 + risk
            else:
                # Pursue; also avoid getting stuck near obstacles.
                score = -dist_opp * 10 + risk
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    return best if best is not None else [0, 0]