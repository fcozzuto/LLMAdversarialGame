def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", [])
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources_raw = observation.get("resources", [])
    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]
    best = None

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        opp_d = man(nx, ny, ox, oy)
        if resources:
            rd = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < rd:
                    rd = d
        else:
            rd = 0

        # Prefer getting closer to resources; also keep away from opponent; slight bias to stay.
        score = -rd - 2 * (0 if opp_d == 0 else opp_d) + (1 if dx == 0 and dy == 0 else 0)
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]