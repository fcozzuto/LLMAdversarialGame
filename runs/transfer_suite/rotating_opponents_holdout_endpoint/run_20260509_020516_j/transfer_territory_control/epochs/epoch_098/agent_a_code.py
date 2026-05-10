def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H:
            unclaimed.add((x, y))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H:
            oppT.add((x, y))

    if not oppT and observation.get("opponent_territory_count", 0) == 0:
        oppT = set()

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H

    best = [0, 0]
    best_s = -10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        d_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        s = 0

        if (nx, ny) in unclaimed:
            s += 5e5
        if (nx, ny) in oppT:
            s += 2e6  # flipping on entry: immediate swing

        # Attack: reduce distance to opponent territory (or opponent position if no territory yet)
        if oppT:
            md = 10**9
            for ax, ay in oppT:
                dd = (ax - nx) * (ax - nx) + (ay - ny) * (ay - ny)
                if dd < md:
                    md = dd
            s += max(0, 2000 - md)
        else:
            md = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            s += max(0, 1000 - md)

        # Avoid getting stuck chasing behind: slightly prefer moves that make progress to center
        s += -0.6 * d_center

        # Small anti-bounce: prefer not to move directly away from center too hard
        s += 0.05 * (d_center - ((sx - cx) * (sx - cx) + (sy - cy) * (sy - cy)))

        if s > best_s or (s == best_s and (dx, dy) < (best[0], best[1])):
            best_s = s
            best = [dx, dy]

    return best