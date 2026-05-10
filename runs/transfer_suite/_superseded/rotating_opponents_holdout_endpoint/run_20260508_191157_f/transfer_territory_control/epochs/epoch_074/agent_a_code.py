def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: closest unclaimed; if none, grab nearest opponent territory.
    targets = list(unclaimed) if unclaimed else list(opp_terr)
    if not targets:
        return [0, 0]

    tx, ty = min(targets, key=lambda t: (md(sx, sy, t[0], t[1]), t[1], t[0]))
    best_move = (0, 0)
    best_val = -10**9

    # Simple deterministic scoring for the next step.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = md(nx, ny, tx, ty)
        val = -d_to_target

        if (nx, ny) in unclaimed:
            val += 30
        if (nx, ny) in opp_terr:
            val += 10  # flipping into opponent territory

        # Keep pressure without getting stuck: avoid moving away from target when possible.
        d_now = md(sx, sy, tx, ty)
        if d_to_target < d_now:
            val += 6
        elif d_to_target > d_now + 1:
            val -= 4

        # Small anti-opponent bias: prefer increasing distance from opponent.
        if md(nx, ny, ox, oy) > md(sx, sy, ox, oy):
            val += 2

        # Deterministic tie-break: prefer staying only if equal, else lexicographic.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]