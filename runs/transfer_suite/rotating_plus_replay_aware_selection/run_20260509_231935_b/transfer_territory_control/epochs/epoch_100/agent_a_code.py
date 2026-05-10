def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    targets = unclaimed
    if not targets:
        targets = []
        for (tx, ty) in opp_terr:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                nx, ny = tx + dx, ty + dy
                if inside(nx, ny) and (nx, ny) not in obs and (nx, ny) not in opp_terr:
                    targets.append((nx, ny))
        if not targets:
            targets = list(unclaimed)  # still empty possible

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    t_near = None
    if targets:
        t_near = min(targets, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        d_to_opp = dist(nx, ny, ox, oy)
        val += d_to_opp * 0.08  # prefer staying away slightly (edge-claimer opponent)
        if t_near is not None:
            val += -dist(nx, ny, t_near[0], t_near[1]) * 1.0

        if (nx, ny) in opp_terr:
            val += 6.0  # flipping on entry is strong

        if (nx, ny) in self_terr:
            val += 0.5  # mild inertia/avoid unnecessary contest

        if (dx, dy) == (0, 0):
            val -= 0.12  # discourage full stalling when moves exist

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]