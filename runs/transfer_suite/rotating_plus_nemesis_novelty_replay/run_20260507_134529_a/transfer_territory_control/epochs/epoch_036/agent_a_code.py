def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    best_d = None
    best_v = -10**18

    # Values designed to aggressively intercept and steal opponent cells when possible.
    # Territory flipping on entry is True, so moving onto opponent territory is primary.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not opp_terr:
        # If opponent territory unknown/empty, push toward opponent position while avoiding obstacles.
        target = (ox, oy)
        opp_terr = set()

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        v = 0

        # Immediate flip/claim incentives
        if cell in opp_terr:
            v += 1000000
        elif cell in self_terr:
            v += 10
        elif cell in unclaimed:
            v += 200
        else:
            v += 40  # covers cases not in lists

        # Interception pressure: prefer moves that reduce distance to nearest opponent territory (or opponent position)
        if opp_terr:
            # compute nearest territory distance from next cell
            dmin = 10**9
            for tx, ty in opp_terr:
                d = abs(tx - nx) + abs(ty - ny)
                if d < dmin:
                    dmin = d
            v += 500 - 20 * dmin
        else:
            d = abs(ox - nx) + abs(oy - ny)
            v += 300 - 20 * d

        # Anti-suicide: avoid getting trapped closer to obstacles locally
        # (use a small penalty if next cell has many adjacent obstacles)
        adj_obs = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_obs += 1
        v -= 5 * adj_obs

        # Small tie-break: deterministic preference toward diagonal when equally good
        v += -0.001 * (abs(dx) + abs(dy))

        if v > best_v:
            best_v = v
            best_d = [dx, dy]

    if best_d is None:
        return [0, 0]
    return best_d