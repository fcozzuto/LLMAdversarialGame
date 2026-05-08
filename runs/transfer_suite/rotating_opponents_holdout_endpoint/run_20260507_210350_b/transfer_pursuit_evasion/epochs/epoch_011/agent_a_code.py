def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Predict opponent next position using 1-step lookahead with same movement constraints.
    best_o = (ox, oy)
    best_score_o = -10**18 if pursuer else 10**18  # if we're pursuer, opponent tries to maximize our distance
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny):
            nx, ny = ox, oy
        d = cheb(nx, ny, sx, sy)
        score = d
        # deterministic tie-break: prefer moves that keep opponent away but also reduce "oscillation"
        if pursuer:
            if score > best_score_o or (score == best_score_o and (nx, ny) < best_o):
                best_score_o, best_o = score, (nx, ny)
        else:
            if score < best_score_o or (score == best_score_o and (nx, ny) < best_o):
                best_score_o, best_o = score, (nx, ny)

    tx, ty = best_o

    # If pursuer: go toward predicted opponent. If evader: go away from predicted pursuer.
    best_m = (0, 0)
    best_score = -10**18 if pursuer else 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        d = cheb(nx, ny, tx, ty)
        # extra: avoid standing next to obstacles (often causes getting cornered)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    near += 1
        score = (-d if pursuer else d) - (0.05 * near)
        if pursuer:
            if score > best_score:
                best_score, best_m = score, (dx, dy)
        else:
            if score < best_score:
                best_score, best_m = score, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]