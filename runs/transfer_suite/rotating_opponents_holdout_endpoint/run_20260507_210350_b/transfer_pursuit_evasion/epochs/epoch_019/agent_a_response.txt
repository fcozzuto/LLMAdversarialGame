def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def min_obs_dist(nx, ny):
        md = 10**9
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d < md: md = d
        return md if md != 10**9 else 99

    best = None
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        obs_clear = min_obs_dist(nx, ny)
        # Avoid stepping adjacent to obstacles; deterministic tie-break by deltas order
        if pursuer:
            # primary: minimize distance to opponent; secondary: keep away from obstacles
            score = (-d * 1000) + (obs_clear * 10) - (dx == 0 and dy == 0) * 1
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # primary: maximize distance from opponent; secondary: keep away from obstacles
            score = (d * 1000) + (obs_clear * 10) - (dx == 0 and dy == 0) * 1
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # If all moves invalid, stay still (engine keeps in place on invalid moves).
        return [0, 0]
    return [best[0], best[1]]