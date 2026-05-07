def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    tr = observation.get("turns_remaining", 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manhattan(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        # Move toward midline to better compete with sweeping patterns.
        target = (w // 2, h // 2)
        best = [0, 0]
        best_key = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not step_ok(nx, ny): 
                continue
            # Also avoid moving toward opponent too strongly.
            d_opp = manhattan(nx, ny, ox, oy)
            d_mid = manhattan(nx, ny, target[0], target[1])
            key = (-d_opp, d_mid, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_key = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny): 
            continue
        # Evaluate the best resource after taking this move.
        best_cell_key = None
        for rx, ry in resources:
            self_d = manhattan(nx, ny, rx, ry)
            opp_d = manhattan(ox, oy, rx, ry)
            # "Time" in turns with unit speed; diagonal allowed so manhattan is a safe lower bound.
            self_t = self_d
            opp_t = opp_d
            # Prefer cells we can reach earlier; otherwise minimize lateness.
            lead = opp_t - self_t
            # If we're behind, prefer making the gap larger (deny opponent).
            tie_break = (abs(self_t - opp_t), self_d, -lead)
            cell_key = (-lead, tie_break, rx, ry)
            if best_cell_key is None or cell_key < best_cell_key:
                best_cell_key = cell_key
        # Secondary: avoid giving opponent immediate access to some resource by increasing their average distance.
        opp_dist_sum = 0
        for rx, ry in resources:
            opp_dist_sum += manhattan(ox, oy, rx, ry)
        # But deterministic and cheap: use only opponent distance to the chosen best resource implied by best_cell_key.
        # We re-derive chosen resource deterministically by max score against current position.
        chosen = None
        for rx, ry in resources:
            self_d0 = manhattan(nx, ny, rx, ry)
            opp_d0 = manhattan(ox, oy, rx, ry)
            lead0 = opp_d0 - self_d0
            key0 = (-lead0, abs(self_d0 - opp_d0), self_d0, rx, ry)
            if chosen is None or key0 < chosen[0]:
                chosen = (key0, rx, ry, lead0)
        rx, ry = chosen[1], chosen[2]
        # Encourage moving toward chosen resource and not colliding with "stagnation" near.
        key = (best_cell_key, manhattan(nx, ny, rx, ry), -manhattan(nx, ny, ox, oy), tr, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move