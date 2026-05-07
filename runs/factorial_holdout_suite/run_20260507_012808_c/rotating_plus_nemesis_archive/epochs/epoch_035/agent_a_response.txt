def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    env = observation.get("environment_name", "")
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                valid.append((x, y))
    if not valid:
        return [0, 0]

    # Prefer resources we can reach no later than opponent; then minimize (opp_dist - self_dist).
    def target_score(t):
        tx, ty = t
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = sd - od  # negative is good for us
        # tie-break: earlier and bigger lead on resource_collection
        tieb = 0 if env != "resource_collection" else sd
        return (0 if lead <= 0 else 1, lead, tieb, sd, tx, ty)

    valid.sort(key=target_score)
    tx, ty = valid[0]

    # Move one step toward target; avoid obstacles deterministically.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    dirs = [(dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy), (0, 0)]
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(mx), int(my)]

    return [0, 0]