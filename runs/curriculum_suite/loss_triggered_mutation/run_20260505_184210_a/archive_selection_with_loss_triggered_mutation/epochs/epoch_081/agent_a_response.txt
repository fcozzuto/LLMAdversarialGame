def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        dx, dy = sign(tx - sx), sign(ty - sy)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    # Prefer resources where we are relatively closer than the opponent.
    tx, ty = min(resources, key=lambda r: (man(me, r) - man(opp, r), man(me, r), r[0], r[1]))

    dx = sign(tx - sx)
    dy = sign(ty - sy)

    # Try diagonal first, then axis moves, deterministic order.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if valid(nx, ny):
            return [int(mx), int(my)]

    return [0, 0]