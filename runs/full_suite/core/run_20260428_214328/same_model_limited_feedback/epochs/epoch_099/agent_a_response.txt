def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        def md(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        target = min(resources, key=lambda r: (md((sx, sy), r), r[0], r[1]))
        tx, ty = target
        dist_t = lambda x, y: abs(tx - x) + abs(ty - y)
        dist_o = lambda x, y: abs(ox - x) + abs(oy - y)

        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                val = (-dist_t(nx, ny), dist_o(nx, ny), nx - sx, ny - sy)
                if best is None or val > best[0]:
                    best = (val, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # No resources: head toward opponent but keep safe from obstacles
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = (-(abs(ox - nx) + abs(oy - ny)), 0, nx, ny)
            if best is None or val > best[0]:
                best = (val, [dx, dy])
    return best[1] if best is not None else [0, 0]