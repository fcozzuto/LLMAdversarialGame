def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = sorted(moves, key=lambda m: (m[0] == 0 and m[1] == 0, abs(m[0]) + abs(m[1])))

    # Focus on closest resources to keep deterministic and fast
    nearest = sorted(resources, key=lambda r: manh(sx, sy, r[0], r[1]))[:6]

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        imm = 1 if (nx, ny) in res_set else 0

        # Score by how much sooner we can reach a resource than the opponent.
        # Prefer immediate pickup, then maximal lead, then shorter our distance, then closer to opponent (less risk).
        best_lead = -10**9
        best_our_d = 10**9
        best_opp_d = 10**9
        for rx, ry in nearest:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            lead = od - sd
            if lead > best_lead or (lead == best_lead and (sd < best_our_d or (sd == best_our_d and od < best_opp_d))):
                best_lead = lead
                best_our_d = sd
                best_opp_d = od

        score = (imm, best_lead, -best_our_d, -best_opp_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move