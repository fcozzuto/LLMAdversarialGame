def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    # Heuristic: if we look like pursuer, chase; otherwise, evade.
    pursuer = ("pursuer" in self_role) or ("evader" in opp_role) or ("catcher" in self_role)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def score_for(x, y):
        # Base objective: approach or flee.
        d = dist2(x, y, ox, oy)
        # Tie-break: for pursuer, pull toward center; for evader, move away from center.
        dc = (x - cx) * (x - cx) + (y - cy) * (y - cy)
        # Extra obstacle-aware term: prefer positions with more free neighboring cells (deterministic).
        free = 0
        for mx, my in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            nx, ny = x + mx, y + my
            if inb(nx, ny) and (nx, ny) not in obst:
                free += 1
        if pursuer:
            return (d, -free, dc)  # minimize d; maximize free; minimize dc
        else:
            return (-d, -free, -dc)  # maximize d; maximize free; maximize dc

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        key = score_for(nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]