def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    pursuer = any(k in srole for k in ("pursuer", "chaser", "catch", "pursuit")) and not any(k in srole for k in ("evader", "evad"))
    if any(k in orole for k in ("pursuer", "chaser", "catch", "pursuit")):
        pursuer = False

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not free(nx, ny):
            continue
        ddx, ddy = nx - int(ox), ny - int(oy)
        d = ddx * ddx + ddy * ddy
        score = d if pursuer else -d
        if score < best[0] if pursuer else score > best[0]:
            best = (score, dx, dy)
        if score == best[0] and (dx, dy) < (best[1], best[2]):
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0 and free(int(sx), int(sy)) is False:
        for dx, dy in dirs:
            nx, ny = int(sx) + dx, int(sy) + dy
            if free(nx, ny):
                return [dx, dy]
    return [int(best[1]), int(best[2])]