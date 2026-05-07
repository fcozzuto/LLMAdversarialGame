def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_xy(v):
        if isinstance(v, dict):
            x = v.get("x", v.get("posx", v.get("position", (None, None)) and v.get("position")[0]))
            y = v.get("y", v.get("posy", v.get("position", (None, None)) and v.get("position")[1]))
            return x, y
        return v[0], v[1]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = to_xy(p)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = to_xy(r)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    for tx, ty in resources:
        sd = dist((sx, sy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        # Prefer winning race, then shorter self distance, then closer (Chebyshev) to reduce steps
        cd = max(abs(tx - sx), abs(ty - sy))
        candidates.append((od - sd, -sd, -cd, tx, ty))
    candidates.sort(reverse=True)
    _, _, _, tx, ty = candidates[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            score = (-10**9, 0, 0)
        else:
            # Move that most reduces Chebyshev distance to target; also keep opponent pressure in mind
            before = max(abs(tx - sx), abs(ty - sy))
            after = max(abs(tx - nx), abs(ty - ny))
            sd_after = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            score = (od - sd_after, -(after), -sd_after)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]