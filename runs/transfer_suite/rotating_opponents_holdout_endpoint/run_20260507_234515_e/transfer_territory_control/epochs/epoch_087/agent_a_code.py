def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set()
    for p in observation.get("self_territory") or []:
        try:
            self_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - b) + abs(c - d)

    targets = resources if resources else unclaimed
    prefer_unclaimed = not resources and unclaimed

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue

        val = 0
        d_opp = man(ox, nx, oy, ny)

        if targets:
            # maximize closeness to resources; otherwise expand to unclaimed while avoiding opponent
            d_to = min(abs(tx - nx) + abs(ty - ny) for tx, ty in targets)
            if resources:
                val += 5000 - 50 * d_to
            else:
                val += 1200 - 40 * d_to
                if prefer_unclaimed and (nx, ny) in self_terr:
                    val -= 200

        # safety: keep some distance from opponent
        val += 15 * d_opp

        # break ties deterministically toward smaller dx, then smaller dy
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    # if all moves blocked, stay put if possible else pick first feasible
    if cell_ok(sx, sy):
        return best_move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if cell_ok(nx, ny):
            return [dx, dy]
    return [0, 0]